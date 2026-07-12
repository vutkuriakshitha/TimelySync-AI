package com.timelysync.payload.request;

import jakarta.validation.constraints.Size;

public class UpdateProfileRequest {
    @Size(max = 100)
    private String name;

    @Size(max = 500)
    private String bio;

    private String avatar;

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }

    public String getBio() { return bio; }
    public void setBio(String bio) { this.bio = bio; }

    public String getAvatar() { return avatar; }
    public void setAvatar(String avatar) { this.avatar = avatar; }
}
