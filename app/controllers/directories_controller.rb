# frozen_string_literal: true

class DirectoriesController < ApplicationController
  layout 'public'

  before_action :authenticate_user!  # 로그인 필수

  before_action :set_cache_headers
  before_action :set_directory
  before_action :set_title

  def show
    @accounts = @directory.accounts.page(params[:page]).per(20)
  end

  private

  def set_cache_headers
    response.headers['Cache-Control'] = 'no-store'
  end

  def set_directory
    @directory = Directory.new
  end

  def set_title
    @page_title = I18n.t('directories.explore_people')
  end
end