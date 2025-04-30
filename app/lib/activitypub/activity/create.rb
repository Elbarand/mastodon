def perform
  return if Rails.configuration.x.whipping.disable_federation

  # 나머지 ActivityPub 툿 전송 처리
end