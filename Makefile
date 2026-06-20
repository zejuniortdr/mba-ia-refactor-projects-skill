remove-skills:
	@echo "Removing skills..."
	@rm -rf code-smells-project/.claude/skills
	@rm -rf ecommerce-api-legacy/.claude/skills
	@rm -rf task-manager-api/.claude/skills
	@echo "Skills removed successfully!"

update-skills: remove-skills
	@echo ""
	@echo "Updating skills..."

	@mkdir -p code-smells-project/.claude
	@mkdir -p ecommerce-api-legacy/.claude
	@mkdir -p task-manager-api/.claude

	@cp -r ~/.claude/skills code-smells-project/.claude/skills
	@cp -r ~/.claude/skills ecommerce-api-legacy/.claude/skills
	@cp -r ~/.claude/skills task-manager-api/.claude/skills

	@echo "Skills updated successfully!"