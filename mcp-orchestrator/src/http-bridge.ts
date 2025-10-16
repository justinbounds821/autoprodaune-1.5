#!/usr/bin/env node
/**
 * HTTP Bridge for MCP Orchestrator
 * Exposes all MCP tools via REST API for communication with mcp_server
 */

import express, { Request, Response } from 'express';
import dotenv from 'dotenv';
import { LinearClient } from '@linear/sdk';
import { Octokit } from '@octokit/rest';
import { createClient } from '@supabase/supabase-js';
import { chromium } from 'playwright';
import { execSync } from 'child_process';

dotenv.config();

const app = express();
app.use(express.json({ limit: '10mb' }));

// Initialize clients
const getLinearClient = () => {
  const apiKey = process.env.LINEAR_API_KEY;
  if (!apiKey) throw new Error('LINEAR_API_KEY not set');
  return new LinearClient({ apiKey });
};

const getGitHubClient = () => {
  const token = process.env.GITHUB_TOKEN;
  if (!token) throw new Error('GITHUB_TOKEN not set');
  return new Octokit({ auth: token });
};

const getSupabaseClient = () => {
  const url = process.env.SUPABASE_URL;
  const key = process.env.SUPABASE_SERVICE_KEY || process.env.SUPABASE_ANON_KEY;
  if (!url || !key) throw new Error('SUPABASE_URL and key not set');
  return createClient(url, key);
};

// ==================== WORKFLOW ORCHESTRATION ====================

async function orchestrateWorkflow(payload: any) {
  const { command, context, options = {} } = payload;
  const startTime = Date.now();
  const workflowId = `WORKFLOW-${Date.now()}`;

  console.error(`[Workflow ${workflowId}] Starting: ${command}`);

  try {
    const opts = {
      auto_execute: options.auto_execute ?? false,
      create_linear_tasks: options.create_linear_tasks ?? true,
      create_github_issues: options.create_github_issues ?? true,
      generate_report: options.generate_report ?? true,
    };

    // Create plan based on command
    const plan = await createPlan(command, context);
    
    // Create Linear epic
    let epicId: string | undefined;
    const taskResults: any[] = [];
    const agentPrompts: any[] = [];

    if (opts.create_linear_tasks) {
      const linear = getLinearClient();
      const teamId = process.env.LINEAR_TEAM_ID;
      if (!teamId) throw new Error('LINEAR_TEAM_ID not set');

      const project = await linear.createProject({
        name: plan.epic_title,
        description: plan.epic_description,
        teamIds: [teamId],
      });
      const projectData = await project.project;
      epicId = projectData?.id;
      console.error(`[Workflow ${workflowId}] Epic created: ${epicId}`);
    }

    // Create tasks
    for (const taskPlan of plan.tasks) {
      let linearId: string | undefined;

      if (opts.create_linear_tasks) {
        const linear = getLinearClient();
        const teamId = process.env.LINEAR_TEAM_ID;
        const issue = await linear.createIssue({
          teamId: teamId!,
          title: taskPlan.title,
          description: taskPlan.description,
          priority: taskPlan.priority || 0,
          projectId: epicId,
        });
        const issueData = await issue.issue;
        linearId = issueData?.identifier;
      }

      // Create GitHub issue
      let githubIssue: number | undefined;
      if (opts.create_github_issues && linearId) {
        const github = getGitHubClient();
        const [owner, repo] = (process.env.GITHUB_REPO || '').split('/');
        if (owner && repo) {
          const response = await github.issues.create({
            owner,
            repo,
            title: taskPlan.title,
            body: `${taskPlan.description}\n\n**Linear Task**: ${linearId}`,
            labels: taskPlan.labels || [],
          });
          githubIssue = response.data.number;
        }
      }

      // Generate agent prompt
      const prompt = generateAgentPrompt(taskPlan.agent, {
        id: linearId || 'PENDING',
        title: taskPlan.title,
        description: taskPlan.description,
        instructions: taskPlan.instructions,
        files: taskPlan.files,
        success_criteria: taskPlan.success_criteria,
      });

      taskResults.push({
        linear_id: linearId || 'PENDING',
        github_issue: githubIssue,
        title: taskPlan.title,
        agent: taskPlan.agent,
        status: 'pending',
      });

      agentPrompts.push({
        agent: taskPlan.agent,
        task_id: linearId || 'PENDING',
        prompt: prompt,
        estimated_time: taskPlan.estimated_time,
      });
    }

    const executionTime = Date.now() - startTime;

    return {
      ok: true,
      workflow_id: workflowId,
      status: 'completed',
      epic_id: epicId,
      tasks: taskResults,
      agent_prompts: agentPrompts,
      summary: `Created ${taskResults.length} tasks across ${new Set(taskResults.map((t) => t.agent)).size} agents`,
      execution_time_ms: executionTime,
    };
  } catch (error: any) {
    console.error(`[Workflow ${workflowId}] Error:`, error);
    return {
      ok: false,
      error: error.message,
      workflow_id: workflowId,
    };
  }
}

async function createPlan(command: string, context: any) {
  const commandLower = command.toLowerCase();

  if (commandLower.includes('fix') && commandLower.includes('test')) {
    return {
      epic_title: `Critical Fixes Sprint - ${new Date().toISOString().split('T')[0]}`,
      epic_description: `Comprehensive fix and test workflow for: ${command}`,
      tasks: [
        {
          title: 'Test backend health',
          description: 'Verify backend is running and healthy',
          priority: 1,
          labels: ['agent:claude', 'priority:critical'],
          agent: 'claude',
          instructions: [
            'Check if backend is running',
            'Test health endpoint',
            'Verify response is valid',
          ],
          files: ['services/api/app/main.py'],
          success_criteria: 'Backend responds with 200 OK',
          estimated_time: '5 minutes',
        },
        {
          title: 'Test API endpoints',
          description: 'Verify API endpoints are working',
          priority: 1,
          labels: ['agent:claude', 'priority:critical'],
          agent: 'claude',
          instructions: [
            'Test key API endpoints',
            'Verify responses',
            'Check database integration',
          ],
          files: ['services/api/app/routes/'],
          success_criteria: 'All endpoints return valid responses',
          estimated_time: '10 minutes',
        },
      ],
    };
  }

  // Default plan
  return {
    epic_title: `Workflow: ${command}`,
    epic_description: `Automated workflow for: ${command}`,
    tasks: [
      {
        title: command,
        description: `Execute: ${command}`,
        priority: 2,
        labels: ['agent:claude'],
        agent: 'claude',
        instructions: [command],
        files: [],
        success_criteria: 'Task completed successfully',
        estimated_time: '15 minutes',
      },
    ],
  };
}

function generateAgentPrompt(agent: string, task: any): string {
  let prompt = `=== ${agent.toUpperCase()} AGENT ===\n`;
  prompt += `TASK: ${task.id}\n`;
  prompt += `TITLE: ${task.title}\n\n`;
  
  if (task.description) {
    prompt += `DESCRIPTION:\n${task.description}\n\n`;
  }
  
  prompt += `INSTRUCTIONS:\n`;
  task.instructions.forEach((instruction: string, i: number) => {
    prompt += `${i + 1}. ${instruction}\n`;
  });
  prompt += `\n`;
  
  if (task.files && task.files.length > 0) {
    prompt += `FILES:\n`;
    task.files.forEach((file: string) => {
      prompt += `- ${file}\n`;
    });
    prompt += `\n`;
  }
  
  if (task.success_criteria) {
    prompt += `SUCCESS CRITERIA:\n${task.success_criteria}\n\n`;
  }
  
  prompt += `===\n`;
  return prompt;
}

// ==================== LINEAR TOOLS ====================

async function linearCreateTask(payload: any) {
  try {
    const linear = getLinearClient();
    const teamId = payload.team_id || process.env.LINEAR_TEAM_ID;
    if (!teamId) throw new Error('Team ID not provided');

    const issue = await linear.createIssue({
      teamId,
      title: payload.title,
      description: payload.description,
      priority: payload.priority || 0,
      projectId: payload.epic_id,
      assigneeId: payload.assignee,
    });

    const issueData = await issue.issue;
    return {
      ok: true,
      task_id: issueData?.identifier,
      url: `https://linear.app/issue/${issueData?.identifier}`,
    };
  } catch (error: any) {
    return { ok: false, error: error.message };
  }
}

async function linearUpdateTask(payload: any) {
  try {
    const linear = getLinearClient();
    const { task_id, status, comment } = payload;

    await linear.updateIssue(task_id, {
      stateId: status, // Simplified - would need state mapping
    });

    if (comment) {
      await linear.createComment({
        issueId: task_id,
        body: comment,
      });
    }

    return { ok: true, task_id, status };
  } catch (error: any) {
    return { ok: false, error: error.message };
  }
}

async function linearListTasks(payload: any) {
  try {
    const linear = getLinearClient();
    const teamId = process.env.LINEAR_TEAM_ID;
    if (!teamId) throw new Error('LINEAR_TEAM_ID not set');

    const issues = await linear.issues({
      filter: {
        team: { id: { eq: teamId } },
      },
      first: payload.limit || 50,
    });

    const tasks = await Promise.all(
      issues.nodes.map(async (issue) => {
        const state = await issue.state;
        return {
          id: issue.identifier,
          title: issue.title,
          status: state?.name || 'unknown',
          priority: issue.priority,
        };
      })
    );

    return { ok: true, tasks };
  } catch (error: any) {
    return { ok: false, error: error.message };
  }
}

// ==================== GITHUB TOOLS ====================

async function githubCreateIssue(payload: any) {
  try {
    const github = getGitHubClient();
    const [owner, repo] = (process.env.GITHUB_REPO || '').split('/');
    if (!owner || !repo) throw new Error('GITHUB_REPO not configured');

    const response = await github.issues.create({
      owner,
      repo,
      title: payload.title,
      body: payload.body,
      labels: payload.labels || [],
      assignees: payload.assignees || [],
    });

    return {
      ok: true,
      issue_number: response.data.number,
      url: response.data.html_url,
    };
  } catch (error: any) {
    return { ok: false, error: error.message };
  }
}

async function githubCommit(payload: any) {
  try {
    const projectPath = process.env.PROJECT_PATH;
    if (!projectPath) throw new Error('PROJECT_PATH not set');

    let message = payload.message;
    if (payload.linear_task_id) {
      message += ` [${payload.linear_task_id}]`;
    }
    if (payload.github_issue_number) {
      message += ` [#${payload.github_issue_number}]`;
    }

    // Stage files
    if (payload.files && payload.files.length > 0) {
      for (const file of payload.files) {
        execSync(`git add "${file}"`, { cwd: projectPath });
      }
    } else {
      execSync('git add -A', { cwd: projectPath });
    }

    // Commit
    execSync(`git commit -m "${message}"`, { cwd: projectPath });

    const commitHash = execSync('git rev-parse HEAD', { cwd: projectPath })
      .toString()
      .trim();

    return {
      ok: true,
      commit_hash: commitHash.substring(0, 7),
      message,
    };
  } catch (error: any) {
    return { ok: false, error: error.message };
  }
}

// ==================== SUPABASE TOOLS ====================

async function supabaseQuery(payload: any) {
  try {
    const supabase = getSupabaseClient();
    const { table, operation, filters, data, limit } = payload;

    let query: any;

    switch (operation) {
      case 'select':
        query = supabase.from(table).select('*');
        if (filters) {
          for (const [key, value] of Object.entries(filters)) {
            query = query.eq(key, value);
          }
        }
        if (limit) {
          query = query.limit(limit);
        }
        break;

      case 'insert':
        if (!data) {
          throw new Error('Data is required for insert operation');
        }
        query = supabase.from(table).insert(data);
        break;

      case 'update':
        if (!data) {
          throw new Error('Data is required for update operation');
        }
        query = supabase.from(table).update(data);
        if (filters) {
          for (const [key, value] of Object.entries(filters)) {
            query = query.eq(key, value);
          }
        }
        break;

      case 'delete':
        query = supabase.from(table).delete();
        if (filters) {
          for (const [key, value] of Object.entries(filters)) {
            query = query.eq(key, value);
          }
        }
        break;

      default:
        throw new Error(`Unknown operation: ${operation}`);
    }

    const { data: result, error } = await query;
    if (error) throw error;

    return {
      ok: true,
      data: result,
      count: Array.isArray(result) ? result.length : 1,
    };
  } catch (error: any) {
    return { ok: false, error: error.message };
  }
}

async function supabaseVerifyFix(payload: any) {
  try {
    const supabase = getSupabaseClient();
    const { table, expected } = payload;

    let query = supabase.from(table).select('*');
    for (const [key, value] of Object.entries(expected)) {
      query = query.eq(key, value);
    }

    const { data, error } = await query;
    if (error) throw error;

    const found = data && data.length > 0;
    return {
      ok: true,
      verified: found,
      data: found ? data[0] : null,
      message: found ? 'Verification passed' : 'Verification failed',
    };
  } catch (error: any) {
    return { ok: false, error: error.message };
  }
}

// ==================== BROWSER TESTING ====================

async function browserTest(payload: any) {
  let browser: any = null;
  try {
    browser = await chromium.launch({ headless: false });
    const page = await browser.newPage();
    const results: string[] = [];

    for (const step of payload.steps) {
      switch (step.action) {
        case 'goto':
          await page.goto(payload.url || step.value);
          results.push(`✅ Navigated to ${payload.url || step.value}`);
          break;

        case 'click':
          await page.click(step.selector);
          results.push(`✅ Clicked ${step.selector}`);
          break;

        case 'fill':
          await page.fill(step.selector, step.value);
          results.push(`✅ Filled ${step.selector}`);
          break;

        case 'wait':
          const timeout = step.timeout || 3000;
          if (step.selector) {
            await page.waitForSelector(step.selector, { timeout });
            results.push(`✅ Waited for ${step.selector}`);
          } else {
            await page.waitForTimeout(timeout);
            results.push(`✅ Waited ${timeout}ms`);
          }
          break;

        case 'assert':
          const element = await page.$(step.selector);
          if (!element) throw new Error(`Element ${step.selector} not found`);
          if (step.value) {
            const text = await element.textContent();
            if (!text?.includes(step.value)) {
              throw new Error(`Expected "${step.value}" in ${step.selector}`);
            }
          }
          results.push(`✅ Asserted ${step.selector}`);
          break;
      }
    }

    await browser.close();
    return {
      ok: true,
      test_name: payload.test_name,
      results,
      message: 'All tests passed',
    };
  } catch (error: any) {
    if (browser) await browser.close();
    return { ok: false, error: error.message };
  }
}

async function apiTest(payload: any) {
  try {
    const options: any = {
      method: payload.method,
      headers: payload.headers || { 'Content-Type': 'application/json' },
    };

    if (payload.body && ['POST', 'PUT', 'PATCH'].includes(payload.method)) {
      options.body = JSON.stringify(payload.body);
    }

    const response = await fetch(payload.url, options);
    const data = await response.json().catch(() => null);

    const expectedStatus = payload.expected_status || 200;
    const statusOk = response.status === expectedStatus;

    return {
      ok: statusOk,
      status: response.status,
      expected_status: expectedStatus,
      data,
      message: statusOk ? 'API test passed' : 'API test failed',
    };
  } catch (error: any) {
    return { ok: false, error: error.message };
  }
}

// ==================== HEALTH CHECK ====================

async function systemHealthCheck() {
  const results: any = {
    timestamp: new Date().toISOString(),
    overall_status: 'healthy',
    services: {},
  };

  try {
    // Check backend
    const backendUrl = process.env.BACKEND_URL || 'http://127.0.0.1:8011';
    try {
      const response = await fetch(`${backendUrl}/health`);
      const data = await response.json();
      results.services.backend = {
        status: response.ok ? 'healthy' : 'unhealthy',
        url: backendUrl,
      };
    } catch (e: any) {
      results.services.backend = { status: 'down', error: e.message };
      results.overall_status = 'degraded';
    }

    // Check Linear
    if (process.env.LINEAR_API_KEY) {
      try {
        const linear = getLinearClient();
        const viewer = await linear.viewer;
        results.services.linear = {
          status: 'healthy',
          user: viewer.name,
        };
      } catch (e: any) {
        results.services.linear = { status: 'unhealthy', error: e.message };
      }
    }

    // Check GitHub
    if (process.env.GITHUB_TOKEN) {
      try {
        const github = getGitHubClient();
        const { data } = await github.users.getAuthenticated();
        results.services.github = {
          status: 'healthy',
          user: data.login,
        };
      } catch (e: any) {
        results.services.github = { status: 'unhealthy', error: e.message };
      }
    }

    // Check Supabase
    try {
      const supabase = getSupabaseClient();
      const { data, error } = await supabase.from('leads').select('*').limit(1);
      results.services.supabase = {
        status: error ? 'unhealthy' : 'healthy',
      };
    } catch (e: any) {
      results.services.supabase = { status: 'unhealthy', error: e.message };
    }

    return { ok: true, ...results };
  } catch (error: any) {
    return { ok: false, error: error.message };
  }
}

// ==================== MAIN ROUTER ====================

app.post('/mcp/orchestrator/call', async (req: Request, res: Response) => {
  const { tool, payload } = req.body;

  console.error(`[HTTP Bridge] Received request for tool: ${tool}`);

  try {
    let result: any;

    switch (tool) {
      // Workflow
      case 'orchestrate_workflow':
        result = await orchestrateWorkflow(payload);
        break;

      // Linear
      case 'linear_create_task':
        result = await linearCreateTask(payload);
        break;
      case 'linear_update_task':
        result = await linearUpdateTask(payload);
        break;
      case 'linear_list_tasks':
        result = await linearListTasks(payload);
        break;

      // GitHub
      case 'github_create_issue':
        result = await githubCreateIssue(payload);
        break;
      case 'github_commit':
        result = await githubCommit(payload);
        break;

      // Supabase
      case 'supabase_query':
        result = await supabaseQuery(payload);
        break;
      case 'supabase_verify_fix':
        result = await supabaseVerifyFix(payload);
        break;

      // Testing
      case 'browser_test':
        result = await browserTest(payload);
        break;
      case 'api_test':
        result = await apiTest(payload);
        break;

      // Health
      case 'system_health_check':
        result = await systemHealthCheck();
        break;

      default:
        result = { ok: false, error: `Unknown tool: ${tool}` };
    }

    res.json(result);
  } catch (error: any) {
    console.error(`[HTTP Bridge] Error executing ${tool}:`, error);
    res.status(500).json({ ok: false, error: error.message });
  }
});

// Health endpoint for the bridge itself
app.get('/health', (req: Request, res: Response) => {
  res.json({
    status: 'ok',
    service: 'mcp-orchestrator-http-bridge',
    timestamp: new Date().toISOString(),
  });
});

// Start server
const PORT = parseInt(process.env.ORCHESTRATOR_HTTP_PORT || '3030');
app.listen(PORT, () => {
  console.error(`✅ MCP Orchestrator HTTP Bridge running on http://127.0.0.1:${PORT}`);
  console.error(`   Available tools: orchestrate_workflow, linear_*, github_*, supabase_*, browser_test, api_test, system_health_check`);
});

