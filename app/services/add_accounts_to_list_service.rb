# frozen_string_literal: true

class AuthorizeFollowService < BaseService
  def call(target_account, source_account, message = nil)
    return nil if Rails.configuration.x.whip.silo_mode

    return nil unless target_account.locked?

    follow_request = FollowRequest.create!(account: source_account, target_account: target_account)
    ActivityPub::DeliveryWorker.perform_async(follow_request.id, source_account.id, 'Follow')
    follow_request
  end
end