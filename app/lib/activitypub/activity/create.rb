# frozen_string_literal: true

class AccountsController < ApplicationController
  layout 'public'

  before_action :set_account
  before_action :set_instance_presenter
  before_action :authenticate_user!, only: [:show]

  def show
    @statuses = @account.statuses
                        .without_reblogs
                        .without_replies
                        .where(visibility: [:public, :unlisted])
                        .limit(20)
                        .to_a
  end

  private

  def set_account
    @account = Account.find_local!(params[:username])
  end

  def set_instance_presenter
    @instance_presenter = InstancePresenter.new
  end
end