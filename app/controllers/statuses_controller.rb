# frozen_string_literal: true

class StatusesController < ApplicationController
  include SignatureVerification
  include RateLimitHeaders

  layout 'public'

  before_action :set_status
  before_action :set_cache_headers
  before_action :set_link_headers
  before_action :check_silenced_account
  before_action :check_chuchu_mode!

  def show
    respond_to do |format|
      format.html do
        expires_in(0, public: true) if user_signed_in?
        fresh_when(etag: @status, last_modified: @status.updated_at)
      end
      format.json do
        render json: @status, serializer: REST::StatusSerializer
      end
    end
  end

  private

  def set_status
    @status = Status.find(params[:id])
  end

  def set_cache_headers
    response.headers['Cache-Control'] = 'no-store'
  end

  def set_link_headers
    return unless @status.thread?

    response.headers['Link'] = "<#{short_account_status_url(@status.account, @status)}>; rel=\"canonical\""
  end

  def check_silenced_account
    not_found if @status.account.silenced?
  end

  def check_chuchu_mode!
    if Rails.configuration.x.chuchu.silo_mode && !user_signed_in?
      not_found
    end
  end
end