#!/bin/bash
# GitHub Access Token 설정 스크립트

echo "================================================"
echo "GitHub Access Token 설정"
echo "================================================"

# 토큰 입력
read -p "GitHub Personal Access Token을 입력하세요: " GITHUB_TOKEN

# 토큰 검증 (형식 체크)
if [[ ! $GITHUB_TOKEN =~ ^(ghp_|github_pat_)[a-zA-Z0-9_]+ ]]; then
    echo "❌ 잘못된 토큰 형식입니다."
    echo "토큰은 'ghp_' 또는 'github_pat_'로 시작해야 합니다."
    exit 1
fi

echo ""
echo "토큰 검증 중..."

# GitHub API로 토큰 테스트
RESPONSE=$(curl -s -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user)

# API 응답 확인
if echo "$RESPONSE" | grep -q "login"; then
    USERNAME=$(echo "$RESPONSE" | grep -o '"login": *"[^"]*"' | cut -d'"' -f4)
    echo "✅ 토큰 검증 성공!"
    echo "   사용자: $USERNAME"
    echo ""

    # 환경 변수 설정 (현재 세션)
    export GITHUB_ACCESS_TOKEN="$GITHUB_TOKEN"
    echo "✅ 현재 세션에 환경 변수 설정 완료"

    # .bashrc에 추가 (영구 설정)
    if ! grep -q "GITHUB_ACCESS_TOKEN" ~/.bashrc 2>/dev/null; then
        echo "" >> ~/.bashrc
        echo "# GitHub Access Token" >> ~/.bashrc
        echo "export GITHUB_ACCESS_TOKEN=\"$GITHUB_TOKEN\"" >> ~/.bashrc
        echo "✅ ~/.bashrc에 추가 완료 (영구 설정)"
        echo "   다음 로그인부터 자동으로 설정됩니다"
    else
        echo "⚠️  ~/.bashrc에 이미 GITHUB_ACCESS_TOKEN이 존재합니다"
        read -p "덮어쓰시겠습니까? (y/n): " OVERWRITE
        if [[ $OVERWRITE == "y" ]]; then
            sed -i '/GITHUB_ACCESS_TOKEN/d' ~/.bashrc
            echo "" >> ~/.bashrc
            echo "# GitHub Access Token" >> ~/.bashrc
            echo "export GITHUB_ACCESS_TOKEN=\"$GITHUB_TOKEN\"" >> ~/.bashrc
            echo "✅ 토큰이 업데이트되었습니다"
        fi
    fi

    echo ""
    echo "================================================"
    echo "설정 완료!"
    echo "================================================"
    echo "다음 명령으로 확인하세요:"
    echo "  echo \$GITHUB_ACCESS_TOKEN"
    echo ""

else
    echo "❌ 토큰 검증 실패"
    echo "응답: $RESPONSE"
    exit 1
fi
