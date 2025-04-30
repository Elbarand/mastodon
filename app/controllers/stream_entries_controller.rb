# frozen_string_literal: true

class StreamEntriesController < ApplicationController
  include SignatureVerification
  include WebAppControllerConcern

  before_action :set_account
  before_action :authenticate_user!, if: :chuchu_silo_mode?

  def show
    @status = @account.statuses.with_includes.find(params[:id])
    authorize @status, :show?

    fresh_when @status
  end

  private

  def set_account
    @account = Account.find_local!(params[:account_username])
  end

  def chuchu_silo_mode?
    Rails.configuration.x.chuchu.silo_mode && !user_signed_in?
  end
end