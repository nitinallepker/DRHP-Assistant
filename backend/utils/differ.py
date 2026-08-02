import difflib
from typing import Dict

class DiffEngine:
    """
    DiffEngine handles comparison between different section drafts,
    returning both raw unified diffs and styled HTML inline reports.
    """

    def generate_diff(self, text_from: str, text_to: str) -> Dict[str, str]:
        """
        Generates comparison between text_from and text_to.
        Returns:
            {
                "raw_diff": "Raw unified patch output",
                "html_diff": "Inline soft-colored HTML report"
            }
        """
        lines_from = text_from.splitlines() if text_from else []
        lines_to = text_to.splitlines() if text_to else []
        
        # 1. Compute Raw Unified Diff
        diff_generator = difflib.unified_diff(
            lines_from, 
            lines_to, 
            fromfile="base_version", 
            tofile="target_version",
            lineterm=""
        )
        raw_diff_str = "\n".join(list(diff_generator))
        
        # 2. Compute Custom Styled Inline HTML report
        # Re-run diff generator to build clean inline html blocks
        diff_lines = difflib.unified_diff(
            lines_from, 
            lines_to, 
            lineterm=""
        )
        
        html_blocks = []
        for line in diff_lines:
            if line.startswith("+++") or line.startswith("---") or line.startswith("@@"):
                html_blocks.append(
                    f"<div style='color: #6a737d; font-style: italic; background-color: #f6f8fa; padding: 2px 8px; border-left: 4px solid #e1e4e8;'>{line}</div>"
                )
            elif line.startswith("+"):
                # Soft green background for added lines
                html_blocks.append(
                    f"<div style='background-color: #e6ffec; color: #22863a; padding: 2px 8px; border-left: 4px solid #28a745;'><b>+</b> {line[1:]}</div>"
                )
            elif line.startswith("-"):
                # Soft red background with line-through for deleted lines
                html_blocks.append(
                    f"<div style='background-color: #ffebe9; color: #cb2431; padding: 2px 8px; border-left: 4px solid #d73a49; text-decoration: line-through;'><b>-</b> {line[1:]}</div>"
                )
            else:
                # Standard line
                html_blocks.append(
                    f"<div style='padding: 2px 8px; color: #24292e; border-left: 4px solid transparent;'>&nbsp;&nbsp;{line}</div>"
                )
                
        html_report = (
            "<div style='font-family: SFMono-Regular, Consolas, \"Liberation Mono\", Menlo, monospace; "
            "font-size: 12px; line-height: 1.6; border: 1px solid #e1e4e8; border-radius: 6px; overflow: hidden; "
            "background-color: #ffffff; white-space: pre-wrap; word-break: break-all;'>"
            + "".join(html_blocks) +
            "</div>"
        )
        
        return {
            "raw_diff": raw_diff_str,
            "html_diff": html_report
        }
