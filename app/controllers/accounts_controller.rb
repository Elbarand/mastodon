# frozen_string_literal: true

class AccountsController < ApplicationController
  include AccountControllerConcern
  include SignatureVerification
  include RateLimitHeaders

  layout 'public'

  before_action :set_account
  before_action :check_account_suspension
  before_action :set_cache_headers
  before_action :check_chuchu_mode!

  def show
    respond_to do |format|
      format.html do
        expires_in(0, public: true) if user_signed_in?
        fresh_when(etag: @account, last_modified: @account.updated_at)
      end

      format.json do
        render json: @account, serializer: REST::AccountSerializer
      end
    end
  end

  private

  def set_account
    @account = Account.find_local!(params[:username])
  end

  def set_cache_headers
    response.headers['Cache-Control'] = 'no-store'
  end

  def check_account_suspension
    not_found if @account.suspended?
  end

  def check_chuchu_mode!
    if Rails.configuration.x.chuchu.silo_mode && !user_signed_in?
      not_found
    end
  end
end