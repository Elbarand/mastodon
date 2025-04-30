# frozen_string_literal: true

class TagsController < ApplicationController
  layout 'public'

  before_action :authenticate_user!

  def show
    @tag = Tag.find_normalized!(params[:id])
    @statuses = []
    @accounts = []
    @hashtags = []
  end
end