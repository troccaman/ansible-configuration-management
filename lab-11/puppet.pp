package { 'nginx':
  ensure => installed,
}

file { '/etc/nginx/sites-available/default':
  ensure  => file,
  content => 'server { listen 80; }',
  require => Package['nginx'],
}