class ActivityPub::DeliveryWorker
  include Sidekiq::Worker

  def perform(status_id, ...)
    return if Rails.configuration.x.whipping.disable_federation # 연합 차단

    # 원래 로직 수행
  end
end