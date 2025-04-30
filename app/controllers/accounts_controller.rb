# frozen_string_literal: true

class AccountsController < ApplicationController
  include SignatureVerification
  include AccountControllerConcern
  include WebAppControllerConcern
  include Authorization

  before_action :set_account
  before_action :check_account_suspension
  before_action :authenticate_user!, if: :limited_federation_mode?
  before_action :set_instance_presenter
  before_action :redirect_new_user
  before_action :set_tab
  before_action :set_statuses
  before_action :set_media_attachments, if: -> { @tab == 'media' }
  before_action :set_tag, if: -> { @tab == 'tagged' }
  before_action :set_search_params, if: -> { @tab == 'search' }
  before_action :redirect_silo_mode_if_needed, only: [:show]

  layout 'public'

  def show
    respond_to do |format|
      format.html do
        expires_in(15.seconds, public: true, stale_while_revalidate: 30.seconds, stale_if_error: 1.hour) unless user_signed_in?
        render :show
      end

      format.rss do
        expires_in 0, public: true
        render layout: false
      end

      format.json do
        expires_in 3.minutes, public: public_fetch_mode?
        render json: @account, serializer: REST::AccountSerializer, relationships: AccountRelationshipsPresenter.new([@account], current_user&.account_id), include: ''
      end
    end
  end

  private

  def set_account
    @account = Account.find_local!(params[:username])
  end

  def check_account_suspension
    gone if @account.suspended?
  end

  def redirect_new_user
    redirect_to about_path if !user_signed_in? && !@account.discoverable?
  end

  def set_tab
    @tab = %w[media with_replies tagged search].include?(params[:tab]) ? params[:tab] : 'statuses'
  end

  def set_instance_presenter
    @instance_presenter = InstancePresenter.new
  end

  def set_statuses
    @statuses = case @tab
    when 'media'
      []
    when 'with_replies'
      @account.statuses.with_replies
    when 'tagged'
      @account.statuses.tagged_with(params[:tag])
    when 'search'
      []
    else
      @account.statuses.where(visibility: [:public, :unlisted])
    end

    @statuses = @statuses.where.not(visibility: :direct) if Rails.configuration.x.chuchu.silo_mode
    @statuses = @statuses.limit(20).to_a if @statuses
  end

  def set_media_attachments
    @media_attachments = @account.media_attachments.attached.limit(10)
  end

  def set_tag
    @tag = Tag.find_by_name(params[:tag])
  end

  def set_search_params
    @search_query = params[:q]
  end

  def redirect_silo_mode_if_needed
    return unless Rails.configuration.x.chuchu.silo_mode
    return if user_signed_in?

    redirect_to new_user_session_path, alert: '로그인한 사용자만 계정 페이지를 볼 수 있습니다.'
  end
end