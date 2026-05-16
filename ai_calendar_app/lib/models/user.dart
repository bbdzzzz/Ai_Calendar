class AppUser {
  final int id;
  final String username;
  final Map<String, dynamic>? preferences;

  AppUser({required this.id, required this.username, this.preferences});

  factory AppUser.fromJson(Map<String, dynamic> json) => AppUser(
    id: json['id'],
    username: json['username'],
    preferences: json['preferences'],
  );

  Map<String, dynamic> toJson() => {
    'id': id,
    'username': username,
    'preferences': preferences,
  };
}
