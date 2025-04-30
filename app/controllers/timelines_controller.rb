# frozen_string_literal: true

class TimelinesController < ApplicationController
  include AccountControllerConcern
  layout 'public'

  before_action :authenticate_user!  # 로그인 필수

  before_action :set_instance_presenter

  def public
    @body_classes = 'with-modals'
    @page_title = I18n.t('statuses.public_timeline')
  end

  def tag
    @tag = Tag.find_normalized!(params[:id])
    @body_classes = 'with-modals'
    @page_title = "##{@tag.name}"
  end
end