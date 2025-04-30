# frozen_string_literal: true

module Api
  module V1
    module Timelines
      class PublicController < Api::BaseController
        before_action :require_user!  # API 접근 차단

        def show
          render json: []
        end
      end
    end
  end
end