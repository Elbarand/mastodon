# frozen_string_literal: true

class StatusesController < ApplicationController
  include SignatureVerification
  include WebAppControllerConcern

  before_action :require_account!
  before_action :set_status, only: [:show, :embed]
  before_action :check_chuchu_mode!
  before_action :redirect_to_original, only: [:show]
  before_action :check_account_suspension, only: [:show]

  def show
    respond_to do |format|
      format.html do
        expires_in(3.minutes, public: public_fetch_mode?)
      end

      format.json do
        render json: @status, serializer: ActivityPub::NoteSerializer, adapter: ActivityPub::Adapter, content_type: 'application/activity+json'
      end
    end
  end

  def embed
    expires_in(3.minutes, public: true)
    render layout: 'embed'
  end

  private

  def set_status
    @status = Status.find(params[:id])
    raise ActiveRecord::RecordNotFound unless @status.distributable?
  end

  def check_chuchu_mode!
    if Rails.configuration.x.chuchu.silo_mode && !user_signed_in?
      not_found
    end
  end

  def redirect_to_original
    redirect_to status_path(@status.reblog), status: :moved_permanently if @status.reblog?
  end

  def check_account_suspension
    not_found if @status.account.suspended?
  end
end