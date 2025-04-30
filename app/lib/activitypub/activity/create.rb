# frozen_string_literal: true

module ActivityPub
  module Activity
    class Create < Base
      include JSONLD

      def perform
        return if delete_arrived_first?
        return if blocked_or_silenced_account?
        return if already_exists?

        if !status.local? && !status.account.local?
          status.distribute!
        elsif status.local? && status.account.local?
          distribute_to_local_followers_only
        end

        forward_activity
      end

      private

      def distribute_to_local_followers_only
        # ✅ federated 전파 차단 (로컬 팔로워에게만 전송)
        FeedManager.instance.populate_home_timelines(status)
        NotificationWorker.push_bulk(status.active_mentions.pluck(:account_id)) do |account_id|
          [account_id, status.id]
        end
      end

      def forward_activity
        # ✅ 외부 인스턴스로의 전파 차단
        return unless status.distributable?

        # 기본 Mastodon에서는 여기서 외부로 전파하지만,
        # 휘핑 스타일에선 주석처리 또는 조건으로 걸러냄
        # ActivityPub::DeliveryWorker.push_bulk(target_inboxes, actor_id: status.account_id, object_id: status.id)
      end
    end
  end
end