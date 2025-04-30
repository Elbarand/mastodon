authenticate :user do
  # 기존 웹 인터페이스 라우트들
end

unauthenticated do
  root to: redirect('/auth/sign_in')
end