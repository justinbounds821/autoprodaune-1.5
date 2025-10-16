/**
 * MCP Orchestrator HTTP Bridge - 732 linii, 12 async functions
 * Express HTTP bridge pe port 3030
 */
import express, { Request, Response } from 'express';
import cors from 'cors';
import { LinearClient } from '@linear/sdk';
import { Octokit } from '@octokit/rest';
import { createClient, SupabaseClient } from '@supabase/supabase-js';
import { chromium, Browser, Page } from 'playwright';
import axios from 'axios';
import * as dotenv from 'dotenv';

dotenv.config();

const app = express();
const PORT = 3030;

// Middleware
app.use(cors());
app.use(express.json());

// Clients
let linearClient: LinearClient;
let githubClient: Octokit;
let supabaseClient: SupabaseClient;
let browser: Browser | null = null;
let page: Page | null = null;

// Initialize clients
async function initializeClients() {
    try {
        // Linear Client
        if (process.env.LINEAR_API_KEY) {
            linearClient = new LinearClient({
                apiKey: process.env.LINEAR_API_KEY
            });
            console.log('✅ Linear client initialized');
        }

        // GitHub Client
        if (process.env.GITHUB_TOKEN) {
            githubClient = new Octokit({
                auth: process.env.GITHUB_TOKEN
            });
            console.log('✅ GitHub client initialized');
        }

        // Supabase Client
        if (process.env.SUPABASE_URL && process.env.SUPABASE_KEY) {
            supabaseClient = createClient(
                process.env.SUPABASE_URL,
                process.env.SUPABASE_KEY
            );
            console.log('✅ Supabase client initialized');
        }

        // Playwright Browser
        browser = await chromium.launch({ headless: true });
        page = await browser.newPage();
        console.log('✅ Playwright browser initialized');

    } catch (error) {
        console.error('❌ Error initializing clients:', error);
    }
}

// ============= HEALTH CHECK =============

app.get('/health', (req: Request, res: Response) => {
    res.json({
        status: 'healthy',
        service: 'mcp_orchestrator',
        version: '1.0.0',
        port: PORT,
        clients: {
            linear: !!linearClient,
            github: !!githubClient,
            supabase: !!supabaseClient,
            playwright: !!browser
        },
        timestamp: new Date().toISOString()
    });
});

// ============= LINEAR ENDPOINTS =============

app.post('/api/tools/linear/create-issue', async (req: Request, res: Response) => {
    try {
        if (!linearClient) {
            return res.status(500).json({ error: 'Linear client not initialized' });
        }

        const { title, description, teamId, priority, labelIds } = req.body;

        const issue = await linearClient.createIssue({
            title,
            description,
            teamId,
            priority: priority || 0,
            labelIds: labelIds || []
        });

        const createdIssue = await issue.issue;
        
        res.json({
            success: true,
            issue: {
                id: createdIssue?.id,
                title: createdIssue?.title,
                url: createdIssue?.url,
                identifier: createdIssue?.identifier
            }
        });
    } catch (error: any) {
        console.error('Error creating Linear issue:', error);
        res.status(500).json({ error: error.message });
    }
});

app.post('/api/tools/linear/update-issue', async (req: Request, res: Response) => {
    try {
        if (!linearClient) {
            return res.status(500).json({ error: 'Linear client not initialized' });
        }

        const { issueId, title, description, stateId, priority } = req.body;

        const updateData: any = {};
        if (title) updateData.title = title;
        if (description) updateData.description = description;
        if (stateId) updateData.stateId = stateId;
        if (priority !== undefined) updateData.priority = priority;

        const result = await linearClient.updateIssue(issueId, updateData);
        const updatedIssue = await result.issue;

        res.json({
            success: true,
            issue: {
                id: updatedIssue?.id,
                title: updatedIssue?.title,
                url: updatedIssue?.url
            }
        });
    } catch (error: any) {
        console.error('Error updating Linear issue:', error);
        res.status(500).json({ error: error.message });
    }
});

app.get('/api/tools/linear/issues', async (req: Request, res: Response) => {
    try {
        if (!linearClient) {
            return res.status(500).json({ error: 'Linear client not initialized' });
        }

        const { teamId, state, limit } = req.query;

        const filter: any = {};
        if (teamId) filter.team = { id: { eq: teamId as string } };
        if (state) filter.state = { name: { eq: state as string } };

        const issues = await linearClient.issues({
            filter,
            first: limit ? parseInt(limit as string) : 50
        });

        const issueList = await Promise.all(
            (issues.nodes || []).map(async (issue) => ({
                id: issue.id,
                title: issue.title,
                description: issue.description,
                url: issue.url,
                identifier: issue.identifier,
                priority: issue.priority,
                state: (await issue.state)?.name
            }))
        );

        res.json({
            success: true,
            issues: issueList,
            count: issueList.length
        });
    } catch (error: any) {
        console.error('Error listing Linear issues:', error);
        res.status(500).json({ error: error.message });
    }
});

// ============= GITHUB ENDPOINTS =============

app.post('/api/tools/github/create-issue', async (req: Request, res: Response) => {
    try {
        if (!githubClient) {
            return res.status(500).json({ error: 'GitHub client not initialized' });
        }

        const { repo, title, body, labels, assignees } = req.body;
        const [owner, repoName] = repo.split('/');

        const { data } = await githubClient.issues.create({
            owner,
            repo: repoName,
            title,
            body,
            labels: labels || [],
            assignees: assignees || []
        });

        res.json({
            success: true,
            issue: {
                id: data.id,
                number: data.number,
                title: data.title,
                url: data.html_url,
                state: data.state
            }
        });
    } catch (error: any) {
        console.error('Error creating GitHub issue:', error);
        res.status(500).json({ error: error.message });
    }
});

app.post('/api/tools/github/create-pr', async (req: Request, res: Response) => {
    try {
        if (!githubClient) {
            return res.status(500).json({ error: 'GitHub client not initialized' });
        }

        const { repo, title, head, base, body } = req.body;
        const [owner, repoName] = repo.split('/');

        const { data } = await githubClient.pulls.create({
            owner,
            repo: repoName,
            title,
            head,
            base: base || 'main',
            body
        });

        res.json({
            success: true,
            pr: {
                id: data.id,
                number: data.number,
                title: data.title,
                url: data.html_url,
                state: data.state
            }
        });
    } catch (error: any) {
        console.error('Error creating GitHub PR:', error);
        res.status(500).json({ error: error.message });
    }
});

app.post('/api/tools/github/commit', async (req: Request, res: Response) => {
    try {
        if (!githubClient) {
            return res.status(500).json({ error: 'GitHub client not initialized' });
        }

        const { repo, branch, message, files } = req.body;
        const [owner, repoName] = repo.split('/');

        // Get current commit SHA
        const { data: refData } = await githubClient.git.getRef({
            owner,
            repo: repoName,
            ref: `heads/${branch}`
        });

        const currentCommitSha = refData.object.sha;

        // Get current commit
        const { data: commitData } = await githubClient.git.getCommit({
            owner,
            repo: repoName,
            commit_sha: currentCommitSha
        });

        const currentTreeSha = commitData.tree.sha;

        // Create blobs for files
        const blobs = await Promise.all(
            files.map(async (file: any) => {
                const { data: blobData } = await githubClient.git.createBlob({
                    owner,
                    repo: repoName,
                    content: Buffer.from(file.content).toString('base64'),
                    encoding: 'base64'
                });
                return {
                    path: file.path,
                    mode: '100644' as const,
                    type: 'blob' as const,
                    sha: blobData.sha
                };
            })
        );

        // Create tree
        const { data: treeData } = await githubClient.git.createTree({
            owner,
            repo: repoName,
            base_tree: currentTreeSha,
            tree: blobs
        });

        // Create commit
        const { data: newCommit } = await githubClient.git.createCommit({
            owner,
            repo: repoName,
            message,
            tree: treeData.sha,
            parents: [currentCommitSha]
        });

        // Update reference
        await githubClient.git.updateRef({
            owner,
            repo: repoName,
            ref: `heads/${branch}`,
            sha: newCommit.sha
        });

        res.json({
            success: true,
            commit: {
                sha: newCommit.sha,
                message: newCommit.message,
                url: newCommit.html_url
            }
        });
    } catch (error: any) {
        console.error('Error creating GitHub commit:', error);
        res.status(500).json({ error: error.message });
    }
});

// ============= SUPABASE ENDPOINTS =============

app.post('/api/tools/supabase/select', async (req: Request, res: Response) => {
    try {
        if (!supabaseClient) {
            return res.status(500).json({ error: 'Supabase client not initialized' });
        }

        const { table, columns, filters, limit } = req.body;

        let query = supabaseClient.from(table).select(columns || '*');

        // Apply filters
        if (filters) {
            Object.entries(filters).forEach(([key, value]) => {
                query = query.eq(key, value);
            });
        }

        // Apply limit
        if (limit) {
            query = query.limit(limit);
        }

        const { data, error } = await query;

        if (error) {
            throw error;
        }

        res.json({
            success: true,
            data,
            count: data?.length || 0
        });
    } catch (error: any) {
        console.error('Error selecting from Supabase:', error);
        res.status(500).json({ error: error.message });
    }
});

app.post('/api/tools/supabase/insert', async (req: Request, res: Response) => {
    try {
        if (!supabaseClient) {
            return res.status(500).json({ error: 'Supabase client not initialized' });
        }

        const { table, data: insertData } = req.body;

        const { data, error } = await supabaseClient
            .from(table)
            .insert(insertData)
            .select();

        if (error) {
            throw error;
        }

        res.json({
            success: true,
            data
        });
    } catch (error: any) {
        console.error('Error inserting to Supabase:', error);
        res.status(500).json({ error: error.message });
    }
});

app.post('/api/tools/supabase/update', async (req: Request, res: Response) => {
    try {
        if (!supabaseClient) {
            return res.status(500).json({ error: 'Supabase client not initialized' });
        }

        const { table, data: updateData, filters } = req.body;

        let query = supabaseClient.from(table).update(updateData);

        // Apply filters
        if (filters) {
            Object.entries(filters).forEach(([key, value]) => {
                query = query.eq(key, value);
            });
        }

        const { data, error } = await query.select();

        if (error) {
            throw error;
        }

        res.json({
            success: true,
            data
        });
    } catch (error: any) {
        console.error('Error updating Supabase:', error);
        res.status(500).json({ error: error.message });
    }
});

app.post('/api/tools/supabase/delete', async (req: Request, res: Response) => {
    try {
        if (!supabaseClient) {
            return res.status(500).json({ error: 'Supabase client not initialized' });
        }

        const { table, filters } = req.body;

        let query = supabaseClient.from(table).delete();

        // Apply filters
        if (filters) {
            Object.entries(filters).forEach(([key, value]) => {
                query = query.eq(key, value);
            });
        }

        const { data, error } = await query.select();

        if (error) {
            throw error;
        }

        res.json({
            success: true,
            data
        });
    } catch (error: any) {
        console.error('Error deleting from Supabase:', error);
        res.status(500).json({ error: error.message });
    }
});

// ============= PLAYWRIGHT ENDPOINTS =============

app.post('/api/tools/playwright/goto', async (req: Request, res: Response) => {
    try {
        if (!page) {
            return res.status(500).json({ error: 'Playwright not initialized' });
        }

        const { url, waitFor } = req.body;

        await page.goto(url, { waitUntil: 'networkidle' });

        if (waitFor) {
            await page.waitForSelector(waitFor);
        }

        res.json({
            success: true,
            url: page.url(),
            title: await page.title()
        });
    } catch (error: any) {
        console.error('Error navigating:', error);
        res.status(500).json({ error: error.message });
    }
});

app.post('/api/tools/playwright/click', async (req: Request, res: Response) => {
    try {
        if (!page) {
            return res.status(500).json({ error: 'Playwright not initialized' });
        }

        const { selector } = req.body;

        await page.click(selector);

        res.json({
            success: true,
            selector,
            url: page.url()
        });
    } catch (error: any) {
        console.error('Error clicking:', error);
        res.status(500).json({ error: error.message });
    }
});

app.post('/api/tools/playwright/fill', async (req: Request, res: Response) => {
    try {
        if (!page) {
            return res.status(500).json({ error: 'Playwright not initialized' });
        }

        const { selector, value } = req.body;

        await page.fill(selector, value);

        res.json({
            success: true,
            selector,
            value
        });
    } catch (error: any) {
        console.error('Error filling:', error);
        res.status(500).json({ error: error.message });
    }
});

app.post('/api/tools/playwright/screenshot', async (req: Request, res: Response) => {
    try {
        if (!page) {
            return res.status(500).json({ error: 'Playwright not initialized' });
        }

        const { path, fullPage } = req.body;

        const screenshot = await page.screenshot({
            path,
            fullPage: fullPage || false
        });

        res.json({
            success: true,
            path: path || 'buffer',
            screenshot: path ? null : screenshot.toString('base64')
        });
    } catch (error: any) {
        console.error('Error taking screenshot:', error);
        res.status(500).json({ error: error.message });
    }
});

// ============= DISCORD ENDPOINTS =============

app.post('/api/tools/discord/send', async (req: Request, res: Response) => {
    try {
        const { content, webhookUrl, embeds } = req.body;
        const url = webhookUrl || process.env.DISCORD_WEBHOOK_URL;

        if (!url) {
            return res.status(400).json({ error: 'Discord webhook URL not configured' });
        }

        const payload: any = { content };
        if (embeds) {
            payload.embeds = embeds;
        }

        const response = await axios.post(url, payload);

        res.json({
            success: true,
            status: response.status
        });
    } catch (error: any) {
        console.error('Error sending Discord message:', error);
        res.status(500).json({ error: error.message });
    }
});

// ============= FILESYSTEM ENDPOINTS =============

import * as fs from 'fs/promises';
import * as path from 'path';

app.post('/api/tools/filesystem/read', async (req: Request, res: Response) => {
    try {
        const { path: filePath } = req.body;

        const content = await fs.readFile(filePath, 'utf-8');

        res.json({
            success: true,
            path: filePath,
            content
        });
    } catch (error: any) {
        console.error('Error reading file:', error);
        res.status(500).json({ error: error.message });
    }
});

app.post('/api/tools/filesystem/write', async (req: Request, res: Response) => {
    try {
        const { path: filePath, content } = req.body;

        // Ensure directory exists
        const dir = path.dirname(filePath);
        await fs.mkdir(dir, { recursive: true });

        await fs.writeFile(filePath, content, 'utf-8');

        res.json({
            success: true,
            path: filePath
        });
    } catch (error: any) {
        console.error('Error writing file:', error);
        res.status(500).json({ error: error.message });
    }
});

// ============= VERCEL ENDPOINTS =============

app.post('/api/tools/vercel/deploy', async (req: Request, res: Response) => {
    try {
        const { projectId, gitBranch } = req.body;
        const vercelToken = process.env.VERCEL_TOKEN;

        if (!vercelToken) {
            return res.status(500).json({ error: 'Vercel token not configured' });
        }

        const response = await axios.post(
            `https://api.vercel.com/v13/deployments`,
            {
                name: projectId,
                gitSource: {
                    type: 'github',
                    ref: gitBranch || 'main'
                }
            },
            {
                headers: {
                    Authorization: `Bearer ${vercelToken}`
                }
            }
        );

        res.json({
            success: true,
            deployment: response.data
        });
    } catch (error: any) {
        console.error('Error deploying to Vercel:', error);
        res.status(500).json({ error: error.message });
    }
});

// ============= RAILWAY ENDPOINTS =============

app.post('/api/tools/railway/deploy', async (req: Request, res: Response) => {
    try {
        const { projectId, environment } = req.body;
        const railwayToken = process.env.RAILWAY_TOKEN;

        if (!railwayToken) {
            return res.status(500).json({ error: 'Railway token not configured' });
        }

        const response = await axios.post(
            `https://backboard.railway.app/graphql/v2`,
            {
                query: `
                    mutation deploymentTrigger($projectId: String!, $environmentId: String!) {
                        deploymentTrigger(input: {
                            projectId: $projectId,
                            environmentId: $environmentId
                        }) {
                            id
                            status
                        }
                    }
                `,
                variables: {
                    projectId,
                    environmentId: environment || 'production'
                }
            },
            {
                headers: {
                    Authorization: `Bearer ${railwayToken}`,
                    'Content-Type': 'application/json'
                }
            }
        );

        res.json({
            success: true,
            deployment: response.data
        });
    } catch (error: any) {
        console.error('Error deploying to Railway:', error);
        res.status(500).json({ error: error.message });
    }
});

// ============= ERROR HANDLING =============

app.use((err: any, req: Request, res: Response, next: any) => {
    console.error('Unhandled error:', err);
    res.status(500).json({
        error: 'Internal server error',
        message: err.message
    });
});

// ============= START SERVER =============

async function startServer() {
    await initializeClients();

    app.listen(PORT, () => {
        console.log('');
        console.log('🚀 ============================================');
        console.log(`🎯 MCP Orchestrator started on port ${PORT}`);
        console.log(`📡 Health check: http://localhost:${PORT}/health`);
        console.log('🔧 Services initialized:');
        console.log(`   - Linear: ${linearClient ? '✅' : '❌'}`);
        console.log(`   - GitHub: ${githubClient ? '✅' : '❌'}`);
        console.log(`   - Supabase: ${supabaseClient ? '✅' : '❌'}`);
        console.log(`   - Playwright: ${browser ? '✅' : '❌'}`);
        console.log('============================================');
        console.log('');
    });
}

// Graceful shutdown
process.on('SIGINT', async () => {
    console.log('\n🛑 Shutting down gracefully...');
    if (browser) {
        await browser.close();
    }
    process.exit(0);
});

startServer().catch(console.error);

export default app;
