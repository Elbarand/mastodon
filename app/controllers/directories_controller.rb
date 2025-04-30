class DirectoriesController < ApplicationController
  layout 'public'

  before_action :authenticate_user!  # 추가
  ...