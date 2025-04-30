# frozen_string_literal: true

class AccountsController < ApplicationController
  include SignatureVerification
  include WebAppControllerConcern

  before_action :require_account!
  before_action :set_account
  before_action :check_chuchu_mode!

  def show
    respond_to do |format|
      format.html do
        expires_in(3.minutes, public: public_fetch_mode?)
      end

      format.json do
        render_with_cache json: @account, serializer: ActivityPub::ActorSerializer, adapter: ActivityPub::Adapter, content_type: 'application/activity+json'
      end
    end
  end

  private

  def set_account
    @account = Account.find_local!(params[:username])
  end

  def check_chuchu_mode!
    if Rails.configuration.x.chuchu.silo_mode && !user_signed_in?
      not_found
    end
  end
end