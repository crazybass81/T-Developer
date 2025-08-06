module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'type-enum': [
      2,
      'always',
      [
        'feat',     // 새로운 기능
        'fix',      // 버그 수정
        'docs',     // 문서 수정
        'style',    // 코드 포맷팅
        'refactor', // 코드 리팩토링
        'test',     // 테스트 추가/수정
        'chore',    // 빌드 프로세스 또는 보조 도구 변경
        'perf',     // 성능 개선
        'ci',       // CI 설정 변경
        'revert',   // 이전 커밋 되돌리기
        'agent'     // 에이전트 관련 변경 (T-Developer 전용)
      ]
    ],
    'subject-case': [2, 'never', ['upper-case']],
    'header-max-length': [2, 'always', 72],
    'body-max-line-length': [2, 'always', 100],
    'scope-enum': [
      2,
      'always',
      [
        'core',
        'agents',
        'api',
        'frontend',
        'infra',
        'docs',
        'tests',
        'deps'
      ]
    ]
  }
};