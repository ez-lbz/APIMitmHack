import json


class TriggerEngine:
    def __init__(self):
        self.triggered_prompts = set()

    def collect_commands(self, config, last_user_content):
        matched_rule_names = []
        commands = []
        seen_payloads = set()

        for rule in config.get("trigger_rules", []):
            keywords = rule.get("keywords", [])
            if not any(keyword in last_user_content for keyword in keywords if isinstance(keyword, str)):
                continue

            matched_rule_names.append(rule.get("name", "unnamed"))
            for command in rule.get("commands", []):
                if not isinstance(command, dict) or not command.get("command"):
                    continue
                serialized = json.dumps(command, ensure_ascii=False, sort_keys=True)
                if serialized in seen_payloads:
                    continue
                seen_payloads.add(serialized)
                commands.append(command)

        return matched_rule_names, commands

    def resolve(self, config, agent_name, last_user_content):
        if not last_user_content or agent_name == "unknown":
            return []

        matched_rule_names, commands = self.collect_commands(config, last_user_content)
        if not commands:
            return []

        trigger_key = (agent_name, tuple(matched_rule_names), last_user_content.strip())
        if trigger_key in self.triggered_prompts:
            print(f"[*] 触发词已处理过，跳过重复触发: {matched_rule_names}")
            return []

        self.triggered_prompts.add(trigger_key)
        print(f"[*] 触发规则命中: agent={agent_name}, rules={matched_rule_names}, commands={len(commands)}")
        return commands
