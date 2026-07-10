from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True, slots=True)
class ParsedDocument:
    original_identifier: str
    title: str
    text: str
    headings: tuple[str, ...] = field(default_factory=tuple)
    paragraphs: tuple[str, ...] = field(default_factory=tuple)
    code_blocks: tuple[str, ...] = field(default_factory=tuple)
    lists: tuple[tuple[str, ...], ...] = field(default_factory=tuple)
    links: tuple[tuple[str, str], ...] = field(default_factory=tuple)
    metadata: dict[str, str] = field(default_factory=dict)


class DocumentParser(Protocol):
    def parse(self, content: str, identifier: str) -> ParsedDocument: ...


class MarkdownParser:
    def parse(self, content: str, identifier: str) -> ParsedDocument:
        lines = content.split("\n")
        title = identifier
        headings: list[str] = []
        paragraphs: list[str] = []
        code_blocks: list[str] = []
        lists: list[tuple[str, ...]] = []
        links: list[tuple[str, str]] = []

        current_paragraph: list[str] = []
        in_code_block = False
        code_buffer: list[str] = []
        current_list: list[str] = []

        for line in lines:
            stripped = line.strip()

            if stripped.startswith("```"):
                if in_code_block:
                    code_blocks.append("\n".join(code_buffer))
                    code_buffer = []
                in_code_block = not in_code_block
                continue

            if in_code_block:
                code_buffer.append(line)
                continue

            if stripped.startswith("#"):
                if current_paragraph:
                    paragraphs.append(" ".join(current_paragraph))
                    current_paragraph = []
                level = len(stripped.split()[0])
                heading_text = stripped.lstrip("#").strip()
                if level == 1 and not title:
                    title = heading_text
                headings.append(heading_text)
                continue

            if stripped.startswith("-") or stripped.startswith("*"):
                item = stripped.lstrip("-* ").strip()
                current_list.append(item)
                continue
            elif current_list:
                lists.append(tuple(current_list))
                current_list = []

            if stripped:
                current_paragraph.append(stripped)
            else:
                if current_paragraph:
                    paragraphs.append(" ".join(current_paragraph))
                    current_paragraph = []

        if current_paragraph:
            paragraphs.append(" ".join(current_paragraph))
        if current_list:
            lists.append(tuple(current_list))
        if code_buffer:
            code_blocks.append("\n".join(code_buffer))

        return ParsedDocument(
            original_identifier=identifier,
            title=title,
            text=content,
            headings=tuple(headings),
            paragraphs=tuple(paragraphs),
            code_blocks=tuple(code_blocks),
            lists=tuple(lists),
            links=tuple(links),
        )


class PlainTextParser:
    def parse(self, content: str, identifier: str) -> ParsedDocument:
        lines = content.strip().split("\n")
        paragraphs: list[str] = []
        current: list[str] = []
        for line in lines:
            if line.strip():
                current.append(line.strip())
            else:
                if current:
                    paragraphs.append(" ".join(current))
                    current = []
        if current:
            paragraphs.append(" ".join(current))
        return ParsedDocument(
            original_identifier=identifier,
            title=identifier,
            text=content,
            paragraphs=tuple(paragraphs),
        )
