# frozen_string_literal: true

class HomeController < ApplicationController
  layout 'public'

  def index
    if Rails.configuration.x.chuchu.silo_mode && !user_signed_in?
      redirect_to new_user_session_path
    end
  end
end