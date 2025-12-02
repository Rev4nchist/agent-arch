# Codebase Map: agent-arch

> Generated: 2025-12-02 10:23:43
> Project Type: 

## Directory Structure

```
|-- .claude/
|   |-- CODEBASE_MAP.md
|   |-- settings.json
|   +-- settings.local.json
|-- .cursor/
|   +-- memories/
|-- .github/
|   +-- workflows/
|       |-- backend-deploy.yml
|       +-- frontend-deploy.yml
|-- .specstory/
|   |-- history/
|   |   +-- 2025-11-24_15-41Z-improve-card-layout-alignment-and-spacing.md
|   |-- .gitignore
|   |-- .project.json
|   +-- .what-is-this.md
|-- .taskmaster/
|   |-- docs/
|   |   |-- ai-guide-persona-test-report.md
|   |   |-- ai-guide-persona-tests.md
|   |   |-- developer-b-coordination.md
|   |   |-- Fourth-Logo.png
|   |   |-- it-admin-request-email.md
|   |   |-- microsoft-sso-auth-prd.md
|   |   |-- remaining-features-prd.md
|   |   |-- role-proposal-ai-architecture-lead.md
|   |   |-- role-proposal-detailed.html
|   |   |-- role-proposal-one-pager.html
|   |   |-- task-13.1-azure-setup-guide.md
|   |   |-- task-13.1-quick-checklist.md
|   |   |-- task-24-deployment-runbook.md
|   |   |-- task-24-infrastructure-assessment.md
|   |   +-- tasks-without-admin-access.md
|   |-- tasks/
|   |   +-- tasks.json
|   |-- config.json
|   +-- state.json
|-- backend/
|   |-- src/
|   |   |-- routers/
|   |   |-- __init__.py
|   |   |-- ai_client.py
|   |   |-- audit_middleware.py
|   |   |-- audit_service.py
|   |   |-- auth.py
|   |   |-- azure_resources_service.py
|   |   |-- blob_service.py
|   |   |-- config.py
|   |   |-- database.py
|   |   |-- indexer.py
|   |   |-- main.py
|   |   |-- main.py.backup
|   |   |-- models.py
|   |   |-- resource_library_service.py
|   |   |-- search_service.py
|   |   +-- snapshot_service.py
|   |-- tests/
|   |   |-- conftest.py
|   |   |-- test_comparison_queries.py
|   |   |-- test_contact_extraction.py
|   |   |-- test_edge_cases.py
|   |   |-- test_fourth_terminology.py
|   |   |-- test_persona_live_queries.py
|   |   |-- test_persona_use_cases.py
|   |   |-- test_response_quality.py
|   |   |-- test_suite_enhancement_plan.md
|   |   |-- test_task19_improvements.py
|   |   +-- test_template_compliance.py
|   |-- .dockerignore
|   |-- .env
|   |-- .env.example
|   |-- add_proposal_endpoints.py
|   |-- add_proposal_model.py
|   |-- add_proposals_container.py
|   |-- AI_Guide_Persona_Test_Report.md
|   |-- deploy-linux.zip
|   |-- Dockerfile
|   |-- nul
|   |-- patch.py
|   |-- README.md
|   |-- requirements.txt
|   |-- requirements-minimal.txt
|   |-- run_bulk_index.py
|   |-- src.zip
|   |-- test_integration.py
|   +-- test_search.py
|-- deploy-check/
|   |-- src/
|   |   |-- routers/
|   |   |-- __init__.py
|   |   |-- ai_client.py
|   |   |-- audit_middleware.py
|   |   |-- audit_service.py
|   |   |-- auth.py
|   |   |-- azure_resources_service.py
|   |   |-- blob_service.py
|   |   |-- config.py
|   |   |-- database.py
|   |   |-- indexer.py
|   |   |-- main.py
|   |   |-- main.py.backup
|   |   |-- models.py
|   |   |-- resource_library_service.py
|   |   |-- search_service.py
|   |   +-- snapshot_service.py
|   |-- .dockerignore
|   |-- Dockerfile
|   +-- requirements.txt
|-- docs/
|   |-- DEPLOYMENT-GUIDE.md
|   |-- MSFT-Integration-Architecture.md
|   +-- REVERSE_PROXY_SETUP.md
|-- frontend/
|   |-- app/
|   |   |-- agents/
|   |   |-- audit/
|   |   |-- budget/
|   |   |-- decisions/
|   |   |-- governance/
|   |   |-- guide/
|   |   |-- meetings/
|   |   |-- resources/
|   |   |-- tasks/
|   |   |-- favicon.ico
|   |   |-- globals.css
|   |   |-- layout.tsx
|   |   +-- page.tsx
|   |-- components/
|   |   |-- guide/
|   |   |-- providers/
|   |   |-- ui/
|   |   |-- Fourth_teal_White_icon.png
|   |   +-- Sidebar.tsx
|   |-- hooks/
|   |   |-- useGuideSuggestions.ts
|   |   +-- usePageContext.ts
|   |-- lib/
|   |   |-- api.ts
|   |   |-- guide-context.ts
|   |   |-- team-members.ts
|   |   +-- utils.ts
|   |-- out/
|   |   |-- _next/
|   |   |-- _not-found/
|   |   |-- 404/
|   |   |-- agents/
|   |   |-- audit/
|   |   |-- budget/
|   |   |-- decisions/
|   |   |-- governance/
|   |   |-- guide/
|   |   |-- meetings/
|   |   |-- resources/
|   |   |-- tasks/
|   |   |-- __next.__PAGE__.txt
|   |   |-- __next._full.txt
|   |   |-- __next._head.txt
|   |   |-- __next._index.txt
|   |   |-- __next._tree.txt
|   |   |-- 404.html
|   |   |-- favicon.ico
|   |   |-- file.svg
|   |   |-- Fourth_icon.png
|   |   |-- globe.svg
|   |   |-- index.html
|   |   |-- index.txt
|   |   |-- next.svg
|   |   |-- staticwebapp.config.json
|   |   |-- vercel.svg
|   |   +-- window.svg
|   |-- public/
|   |   |-- file.svg
|   |   |-- Fourth_icon.png
|   |   |-- globe.svg
|   |   |-- next.svg
|   |   |-- vercel.svg
|   |   +-- window.svg
|   |-- .dockerignore
|   |-- .env.local
|   |-- .env.production
|   |-- .gitignore
|   |-- add_lightbulb_import.py
|   |-- adjust_spacing.py
|   |-- adjust_to_h20.py
|   |-- adjust_to_pt05.py
|   |-- align_bottom_sections.py
|   |-- clean_spacing_approach.py
|   |-- components.json
|   |-- Dockerfile
|   |-- eslint.config.mjs
|   |-- final_alignment.py
|   |-- final_grid_layout.py
|   |-- fix_alignment_final.py
|   |-- fix_card_alignment.py
|   |-- fix_card_alignment_spacing.py
|   |-- fix_card_bottom_alignment.py
|   |-- fix_card_height.py
|   |-- fix_card_text_final.py
|   |-- fix_no_wrap.py
|   |-- fix_tabs_version.py
|   |-- fix_title_height.py
|   |-- fix_top_padding.py
|   |-- fix_with_absolute_positioning.py
|   |-- fixed_height_solution.py
|   |-- increase_top_section_height.py
|   |-- next.config.ts
|   |-- next-env.d.ts
|   |-- package.json
|   |-- package-lock.json
|   |-- patch_dashboard.py
|   |-- patch_dashboard_buttons.py
|   |-- patch_decisions_create.py
|   |-- patch_meetings_autoopen.py
|   |-- patch_package_json.py
|   |-- patch_proposals_decisions.py
|   |-- patch_sidebar.py
|   |-- patch_status.py
|   |-- patch_tasks_autoopen.py
|   |-- postcss.config.mjs
|   |-- README.md
|   |-- reduce_to_pt1.py
|   |-- reduce_top_more.py
|   |-- reduce_top_padding_final.py
|   |-- simple_top_bottom_layout.py
|   |-- staticwebapp.config.json
|   |-- tsconfig.json
|   |-- tsconfig.tsbuildinfo
|   |-- update_dashboard_cards.py
|   |-- use_absolute_positioning.py
|   +-- use_grid_layout.py
|-- logs-extracted/
|   |-- deployments/
|   |   |-- 0ff7b64a-91c7-4e2c-9177-89d7e174c44e/
|   |   |-- 8d55eb80-f26f-4d6f-a46e-d30279dc300e/
|   |   |-- ab2d3ab3-0464-42cc-86a8-6aa5e67c0092/
|   |   |-- aced0294-7ea0-4233-9f65-7640ff79a8ca/
|   |   |-- tools/
|   |   |-- active
|   |   +-- pending
|   +-- LogFiles/
|       |-- Application/
|       |-- AppServiceAppLogs_Feature_Installer/
|       |-- CodeProfiler/
|       |-- kudu/
|       |-- webssh/
|       +-- 2025_12_01_pl1sdlwk00034A_docker.log
|-- logs-new/
|   |-- deployments/
|   |   |-- 0a18ff0c-8ef6-4480-974b-f9d867db5d6b/
|   |   |-- 0ff7b64a-91c7-4e2c-9177-89d7e174c44e/
|   |   |-- 8d55eb80-f26f-4d6f-a46e-d30279dc300e/
|   |   |-- ab2d3ab3-0464-42cc-86a8-6aa5e67c0092/
|   |   |-- aced0294-7ea0-4233-9f65-7640ff79a8ca/
|   |   |-- tools/
|   |   |-- active
|   |   +-- pending
|   +-- LogFiles/
|       |-- Application/
|       |-- AppServiceAppLogs_Feature_Installer/
|       |-- CodeProfiler/
|       |-- kudu/
|       |-- webssh/
|       +-- 2025_12_01_pl1sdlwk00034A_docker.log
|-- scripts/
|   |-- cleanup_test_data.py
|   |-- create-azure-resources.ps1
|   +-- create-azure-resources.sh
|-- webapp-logs/
|   |-- deployments/
|   |   |-- 0ff7b64a-91c7-4e2c-9177-89d7e174c44e/
|   |   |-- 8d55eb80-f26f-4d6f-a46e-d30279dc300e/
|   |   |-- ab2d3ab3-0464-42cc-86a8-6aa5e67c0092/
|   |   |-- aced0294-7ea0-4233-9f65-7640ff79a8ca/
|   |   |-- tools/
|   |   |-- active
|   |   +-- pending
|   +-- LogFiles/
|       |-- Application/
|       |-- AppServiceAppLogs_Feature_Installer/
|       |-- CodeProfiler/
|       |-- kudu/
|       |-- webssh/
|       +-- 2025_12_01_pl1sdlwk00034A_docker.log
|-- .cursorindexingignore
|-- .env
|-- .env.example
|-- .gitignore
|-- AI_Guide_Improvement_Plan.md
|-- AI_Guide_Persona_Test_Report.md
|-- AI_Guide_Test_Report_2025-11-26.md
|-- CURRENT_STATE_AND_TODO.md
|-- debug-cors.bat
|-- Deep-Dive-Foundry-IQ-and-Model-Router.md
|-- deploy-linux.zip
|-- DEVELOPER_A_PROMPT.md
|-- DEVELOPER_B_PROMPT.md
|-- DEVELOPER_C_PROMPT.md
|-- docker-compose.yml
|-- FINAL-Landing-Page-Card-Updates.md
|-- github-secret-AZURE_STATIC_WEB_APPS_API_TOKEN.txt
|-- github-secret-AZURE_WEBAPP_PUBLISH_PROFILE.txt
|-- landing-page.html
|-- logs.zip
|-- logs-new.zip
|-- MSFT-Ignite-2025-Ecosystem-Map.md
|-- nginx.conf
|-- PARALLEL_DEVELOPMENT_SETUP.md
|-- platform-cards-enhancement-report.md
|-- QUICK_START.md
|-- README.md
|-- Resource-Library-Enhancement-Proposal.md
|-- start-dev.bat
|-- start-dev.sh
|-- TASK_8_AZURE_AUTH_REQUIRED.md
|-- TASK_8_COMPLETE.md
|-- TASK_8_IMPLEMENTATION_SUMMARY.md
|-- TASK_8_TEST_RESULTS.md
|-- TASK_9_COMPLETE.md
|-- test_transcript.txt
+-- webapp-logs.zip
```

## Key Directories

- **scripts/**: Scripts (3 files)
- **frontend/**: Frontend application (810 files)
- **backend/**: Backend application (8388 files)
- **.claude/**: Claude config (3 files)
- **docs/**: Documentation (3 files)

## Entry Points



## File Statistics

- **Total Files**: 4962
- **Total Lines**: 1459481

| Extension | Files | Lines |
|-----------|-------|-------|
| .py | 4147 | 1428688 |
| .xml | 154 | 0 |
| .txt | 146 | 0 |
| .typed | 128 | 0 |
| .md | 44 | 10974 |
| .tsx | 42 | 8703 |
| .pyi | 41 | 0 |
| .js | 33 | 178 |
| (no ext) | 32 | 0 |
| .exe | 24 | 0 |

---
*Generated by ClaudeKit Codebase Map | Use with caution - may be outdated*
