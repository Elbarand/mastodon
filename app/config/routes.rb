namespace :admin do
  get 'dm_monitor/:account_id', to: 'dm_monitor#index', as: :dm_monitor
end