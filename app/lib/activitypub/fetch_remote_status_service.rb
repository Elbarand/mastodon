# frozen_string_literal: true

class ActivityPub::FetchRemoteStatusService < BaseService
  def call(uri, id = nil, prefetched_body = nil, protocol = :activitypub)
    return nil if Rails.configuration.x.whip.silo_mode

    body = prefetched_body || fetch_resource(uri)

    return nil if body.nil?

    json = Oj.load(body, mode: :strict)
    ActivityPub::Activity.new(json).perform
  end

  private

  def fetch_resource(uri)
    Request.new(:get, uri).perform.body
  rescue StandardError
    nil
  end
end