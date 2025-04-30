# frozen_string_literal: true

class TimelinesController < ApplicationController
  layout 'public'

  before_action :authenticate_user!, if: :chuchu_silo_mode?

  def public
    @body_classes = 'with-modals'
    render action: 'public'
  end

  def tag
    @tag = Tag.find_normalized!(params[:id])
    @body_classes = 'with-modals'
    render action: 'tag'
  end

  private

  def chuchu_silo_mode?
    Rails.configuration.x.chuchu.silo_mode && !user_signed_in?
  end
end