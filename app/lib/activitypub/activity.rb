# frozen_string_literal: true

class ActivityPub::Activity
  include JsonLdHelper

  attr_reader :json, :account

  def initialize(json, account = nil)
    @json = json
    @account = account
  end

  def perform
    case json['type']
    when 'Create'
      process_create
    when 'Update'
      process_update
    when 'Delete'
      process_delete
    when 'Follow'
      process_follow
    when 'Undo'
      process_undo
    when 'Like'
      process_like
    when 'Announce'
      process_announce
    when 'Block'
      process_block
    when 'Flag'
      process_flag
    else
      nil
    end
  end

  private

  def process_create
    # 기존 게시글 처리
    status = ActivityPub::Activity::Create.new(json, account).perform
    deliver_to_remote_followers if status&.local? && !status.direct_visibility?
  end

  def deliver_to_remote_followers
    return if status.account.local? && Rails.configuration.x.whip.silo_mode

    ActivityPub::DeliveryWorker.perform_async(status.id, status.account_id)
  end

  def status
    @status ||= Status.find_by(uri: json['object']['id'])
  end
end