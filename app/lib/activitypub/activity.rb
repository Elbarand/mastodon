# frozen_string_literal: true

class ActivityPub::Activity
  include JsonLdHelper

  attr_reader :json, :account

  def initialize(json, account = nil)
    @json = json
    @account = account
  end

  def perform
    # ... 기존 코드 유지 ...
  end

  private

  def deliver_to_remote_followers
    return if visibility == :direct
    return if status.account.local? && Rails.configuration.x.whip.silo_mode

    ActivityPub::DeliveryWorker.perform_async(status.id, status.account_id)
  end
end