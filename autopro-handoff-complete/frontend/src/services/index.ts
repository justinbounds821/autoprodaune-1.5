/**
 * Centralized service exports
 * Import services using: import { LeadService, VideoService } from '@/services'
 */

export { default as LeadService } from './LeadService';
export { default as VideoService } from './VideoService';
export { default as AutomationService } from './AutomationService';
export { default as SocialMediaService } from './SocialMediaService';
export { default as FinancialService } from './FinancialService';

// Export types
export type { Lead, CreateLeadDto, LeadStats } from './LeadService';
export type { Video, GenerateVideoDto, VideoStats } from './VideoService';
export type { AutomationStatus, AutomationConfig, AutomationMetrics } from './AutomationService';
export type { SocialPost, CreatePostDto, SocialStats, PlatformStats } from './SocialMediaService';
export type { FinancialDashboard, Revenue, Cost, FinancialMetrics } from './FinancialService';
