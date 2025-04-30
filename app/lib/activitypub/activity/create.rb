# frozen_string_literal: true

module ActivityPub
  module Activity
    class Create < Base
      include JsonLdHelper

      def perform
        ActivityPub 전송을 무시하고 툿 저장만 수행
        Rails.logger.info "ActivityPub 전파 차단: #{status.id}"
      end
    end
  end
end