# frozen_string_literal: true

class Admin::AccountsController < Admin::BaseController
  before_action :set_account, only: [:show, :statuses, :dms]

  def index
    authorize :account, :index?
    @accounts = Account.search(params[:q], limit: 50)
  end

  def show
    authorize @account, :show?
  end

  def statuses
    authorize @account, :show?
    @statuses = @account.statuses.order(id: :desc).page(params[:page]).per(20)
  end

  # ✅ 추가된 관리자용 DM 조회 액션
  def dms
    authorize @account, :show?
    @dms = @account.statuses.where(visibility: :direct).order(id: :desc).page(params[:page]).per(20)
  end

  private

  def set_account
    @account = Account.find(params[:id])
  end
end