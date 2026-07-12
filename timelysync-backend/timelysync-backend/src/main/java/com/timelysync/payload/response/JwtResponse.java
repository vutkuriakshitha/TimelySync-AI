package com.timelysync.payload.response;

public class JwtResponse {
    private String token;
    private String type = "Bearer";
    private UserDto user;

    public JwtResponse(String token, UserDto user) {
        this.token = token;
        this.user = user;
    }

    public String getToken() { return token; }
    public void setToken(String token) { this.token = token; }

    public String getType() { return type; }
    public void setType(String type) { this.type = type; }

    public UserDto getUser() { return user; }
    public void setUser(UserDto user) { this.user = user; }
}
