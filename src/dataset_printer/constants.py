DEFAULT_DATASET = "deepset/prompt-injections"

AUTO_FIELD_PREFERENCES = (
    "text",
    "prompt",
    "prompt_injections",
    "instruction",
    "input",
    "content",
)

AUTO_FIELD_BLOCKLIST = frozenset({"label", "labels", "id", "idx", "metadata"})
