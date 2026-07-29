.PHONY: test validate

test:
	python3 -m unittest discover -s tests -v

validate:
	python3 -m unittest discover -s tests -v
	@test -n "$(SKILL_CREATOR_DIR)" || (echo "Set SKILL_CREATOR_DIR to the skill-creator directory" && exit 2)
	python3 "$(SKILL_CREATOR_DIR)/scripts/quick_validate.py" skills/sleep-routine-coach
