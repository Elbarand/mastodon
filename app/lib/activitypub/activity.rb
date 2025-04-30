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