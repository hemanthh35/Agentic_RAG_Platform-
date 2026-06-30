import re
import logging

logger = logging.getLogger(__name__)


class TextCleaner:
    """Pipeline for cleaning and normalizing extracted document text while maintaining human readability."""

    @classmethod
    def clean(cls, text: str) -> str:
        if not text:
            return ""

        # 1. Normalize line endings to \n
        cleaned = text.replace("\r\n", "\n").replace("\r", "\n")

        # 2. Remove non-printable or unsupported control Unicode chars (except newlines and tabs)
        # Keeps basic Latin, Latin-1 supplement, and spacing/general punctuation
        cleaned = re.sub(r'[^\x09\x0A\x0D\x20-\x7E\xA0-\xFF]', '', cleaned)

        # 3. Trim spacing on each line individually
        lines = [line.strip() for line in cleaned.split("\n")]

        # 4. Collapse duplicate blank lines (maximum 2 consecutive newlines, preserving paragraph boundaries)
        collapsed_lines = []
        for line in lines:
            if line:
                collapsed_lines.append(line)
            else:
                # Add a blank line only if the previous line wasn't already blank (prevents 3+ newlines)
                if collapsed_lines and collapsed_lines[-1] != "":
                    collapsed_lines.append("")

        cleaned_text = "\n".join(collapsed_lines).strip()
        
        logger.info("Successfully completed text cleaning pipeline.")
        return cleaned_text
