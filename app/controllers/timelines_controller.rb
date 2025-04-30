# frozen_string_literal: true

class TimelinesController < ApplicationController
  layout 'public'

  before_action :authenticate_user!

  def home
    redirect_to root_path unless user_signed_in?
  end

  def public
    redirect_to root_path unless user_signed_in?
  end

  def tag
    @tag = Tag.find_normalized!(params[:id])

    redirect_to root_path unless user_signed_in?
  end
end