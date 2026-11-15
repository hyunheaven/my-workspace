"""Render the bundled, immutable field catalog as editable page blocks."""
from __future__ import annotations

import json
from typing import Any
from uuid import uuid4


def _block(block_type: str, content: str) -> dict[str, Any]:
    return {'id': str(uuid4()), 'type': block_type, 'content': content, 'checked': False}


def _table(*rows: list[str]) -> dict[str, Any]:
    return _block('table', json.dumps(rows, ensure_ascii=False, separators=(',', ':')))


def _project_plan_section(field_id: str, label: str, prompt: str) -> list[dict[str, Any]]:
    if field_id == 'goal':
        return [
            _block('heading_2', '주요 목표'),
            _block('bullet', '첫 번째 목표와 성공 기준'),
            _block('bullet', '두 번째 목표와 성공 기준'),
        ]
    if field_id == 'milestones':
        return [
            _block('heading_2', '추진 일정'),
            _table(['Milestone', '담당자', '목표일'], ['첫 번째 산출물', '', '']),
        ]
    if field_id == 'risks':
        return [
            _block('heading_2', '리스크 및 Action Items'),
            _block('paragraph', prompt),
            _block('todo', '리스크별 대응 계획과 담당자 정하기'),
        ]
    return [_block('heading_2', label), _block('paragraph', prompt)]


def template_blocks(template: dict[str, Any]) -> list[dict[str, Any]]:
    if 'blocks' in template:
        return [
            _table(*block['content']) if block['type'] == 'table'
            else _block(block['type'], block['content'])
            for block in template['blocks']
        ]
    is_project_plan = template['id'] == 'pm-plan'
    blocks = (
        [_block('heading_2', '프로젝트 개요'),
         _block('paragraph', '프로젝트 목적과 주요 배경을 입력하세요.')]
        if is_project_plan else [_block('paragraph', template['description'])]
    )
    for field in template['fields']:
        field_id = field['id']
        label = field['label']
        prompt = field.get('placeholder') or '내용을 작성하세요.'
        if is_project_plan:
            blocks.extend(_project_plan_section(field_id, label, prompt))
            continue

        blocks.append(_block('heading_2', label))
        if field['type'] == 'select':
            blocks.extend(_block('bullet', option) for option in field['options'])
        elif field['type'] == 'date':
            blocks.append(_block('paragraph', 'YYYY-MM-DD'))
        elif field_id in {'milestones', 'timeline'} or any(
            word in label for word in ('주요 일정', '중요 일정', '추진 일정', '단계별 일정')
        ):
            blocks.append(_table(['일정', '담당자', '목표일'], ['', '', '']))
        elif any(word in label for word in ('비교 항목', '대안 비교', '요구사항 매핑')):
            blocks.append(_table(['항목', '검토 내용', '판단 근거'], ['', '', '']))
        elif field_id in {'actions', 'next_steps', 'followup'} or any(
            word in label for word in ('할 일', '다음 행동', '다음 단계', '후속 조치', '확인 항목', '체크리스트')
        ):
            blocks.append(_block('todo', prompt))
        else:
            blocks.append(_block('paragraph', prompt))
    return blocks
