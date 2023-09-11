## Baza Backend

API and backend for baza platform. This backend serves API for baza basic income distribution, webwallet, distribution signup and related services.

#### Features

- Basic Income Distribution signup Flow
- Automatic verification for distribution
- Staff dashboard to review/manage distribution profile
- WebWallet for baza coin
  - Has ability to create multiple wallet
  - User can view wallet balance/txs
  - User can send to other wallet address
  - User can receive from other wallet through qr code or wallet address
- User profile section
  - User can manage photo/document/phone number/email
  - Can link social accounts
  - Can enable/disable two factor authentication
- Members page to see other member on platform
- Messenger page to do realtime chat with other members on platform
- Group feature
  - User can create group/join other group
  - Group admin/staff can add news to the group
  - User can add post to group
  - User can add comment to group posts
- Realtime notification for new message, new group content such as new post, news, comment etc
- User can add a hashtag overlay to their image and post social media

#### Tech stacks

- Python
- Django
- Django-Rest-Framework
- Celery
- Django-Channels
