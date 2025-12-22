[x] 1. Install the required packages
[x] 2. Restart the workflow to see if the project is working
[x] 3. Verify the project is working using the feedback tool
[x] 4. Inform user the import is completed and they can start building, mark the import as completed using the complete_project_import tool
[x] 5. Create teams/ directory structure with default-team, playbooks, and profiles
[x] 6. Create team.yaml with activation rules and member configuration
[x] 7. Create playbooks (boot.yaml, on_run_created.yaml, on_chat_message.yaml)
[x] 8. Create persona profile files for all 16 agent roles
[x] 9. Create schemas for team and playbook validation
[x] 10. Create agents registry linking all existing agents
[x] 11. Migrate super-agent files to teams/default-team/orchestrator/
[x] 12. Update registry.yaml with new orchestrator path
[x] 13. Delete original agents/ directory
[x] 14. Fix SuperAgentCore class - add missing service initializations
[x] 15. Fix SuperAgentCore - add initialize() and shutdown() methods
[x] 16. Fix validate_message_envelope return type
[x] 17. Import Incident class from models