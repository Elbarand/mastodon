# frozen_string_literal: true

class AboutController < ApplicationController
  layout 'public'

  before_action :authenticate_user!, if: :chuchu_silo_mode?

  def show
    render layout: 'public'
  end

  private

  def chuchu_silo_mode?
    Rails.configuration.x.chuchu.silo_mode && !user_signed_in?
  end
end