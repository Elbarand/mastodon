# frozen_string_literal: true

class StatusesController < ApplicationController
  layout 'public'

  before_action :authenticate_user! # 로그인 안 하면 접근 불가
  before_action :set_status
  before_action :set_cache_headers

  def show
    expires_in(3.minutes, public: true)
  end

  def embed
    render layout: 'embed'
  end

  private

  def set_status
    @status = Status.find(params[:id])
  end

  def set_cache_headers
    response.headers['Cache-Control'] = 'no-store'
  end
end