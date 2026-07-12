package com.timelysync.payload.response;

public class AccountDto {
    private String id;
    private String name;
    private String email;
    private String avatar;
    private String type;

    public AccountDto() {}

    public AccountDto(String id, String name, String email, String avatar, String type) {
        this.id = id;
        this.name = name;
        this.email = email;
        this.avatar = avatar;
        this.type = type;
    }

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }

    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }

    public String getAvatar() { return avatar; }
    public void setAvatar(String avatar) { this.avatar = avatar; }

    public String getType() { return type; }
    public void setType(String type) { this.type = type; }
}
