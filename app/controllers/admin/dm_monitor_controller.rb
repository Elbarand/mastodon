# frozen_string_literal: true

class Admin::DmMonitorController < Admin::BaseController
  before_action :set_account

  def index
    @direct_messages = @account.statuses.where(visibility: :direct).order(created_at: :desc).limit(50)
  end

  private

  def set_account
    @account = Account.find(params[:account_id])
  end
end