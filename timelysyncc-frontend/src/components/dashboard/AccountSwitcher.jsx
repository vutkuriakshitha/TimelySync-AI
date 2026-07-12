// src/components/dashboard/AccountSwitcher.jsx
import React from 'react';
import { Card, Image, Badge } from 'react-bootstrap';
import { Check, User } from 'lucide-react';

const AccountSwitcher = ({ accounts, currentAccount, onSwitch }) => {
  if (!accounts || accounts.length === 0) {
    return (
      <div className="text-center py-4">
        <User size={48} className="text-muted mb-3" />
        <p className="text-muted">No linked accounts found</p>
      </div>
    );
  }

  return (
    <div className="account-switcher">
      {accounts.map((account) => (
        <Card
          key={account.id}
          className={`mb-3 cursor-pointer transition-all ${account.id === currentAccount?.id ? 'border-primary bg-primary bg-opacity-10' : ''
            }`}
          onClick={() => onSwitch(account.id)}
          style={{ cursor: 'pointer', transition: 'all 0.2s' }}
        >
          <Card.Body className="d-flex align-items-center justify-content-between">
            <div className="d-flex align-items-center gap-3">
              <Image
                src={account.avatar || `https://ui-avatars.com/api/?name=${account.name}&background=0D6EFD&color=fff`}
                roundedCircle
                width="48"
                height="48"
              />
              <div>
                <h6 className="mb-0 fw-semibold">{account.name}</h6>
                <small className="text-muted">{account.email}</small>
                {account.type === 'premium' && (
                  <Badge bg="warning" className="ms-2">Premium</Badge>
                )}
              </div>
            </div>
            {account.id === currentAccount?.id && (
              <Check size={20} className="text-primary" />
            )}
          </Card.Body>
        </Card>
      ))}
    </div>
  );
};

export default AccountSwitcher;