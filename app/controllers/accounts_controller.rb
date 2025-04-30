# frozen_string_literal: true

class AccountsController < ApplicationController
  layout 'public'

  before_action :authenticate_user! # 모든 사용자 페이지 접근 차단
  before_action :set_account

  def show
    # 기본 계정 페이지
  end

  private

  def set_account
    @account = Account.find_local!(params[:username])
  end
end