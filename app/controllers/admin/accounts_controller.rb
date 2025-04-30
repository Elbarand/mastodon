# frozen_string_literal: true

class Admin::AccountsController < Admin::BaseController
  before_action :set_account, only: [:show, :destroy, :dms]

  def index
    @accounts = Account.order(id: :desc).page(params[:page])
  end

  def show
  end

  def destroy
    @account.destroy
    redirect_to admin_accounts_path, notice: I18n.t('admin.accounts.destroyed_msg')
  end

  def dms
    @direct_messages = @account.statuses.where(visibility: :direct).order(id: :desc).limit(50)
  end

  private

  def set_account
    @account = Account.find(params[:id])
  end
end